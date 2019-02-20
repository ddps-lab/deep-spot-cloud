# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""A binary to train CIFAR-10 using a single GPU.

Accuracy:
cifar10_train.py achieves ~86% accuracy after 100K steps (256 epochs of
data) as judged by cifar10_eval.py.

Speed: With batch_size 128.

System        | Step Time (sec/batch)  |     Accuracy
------------------------------------------------------------------
1 Tesla K20m  | 0.35-0.60              | ~86% at 60K steps  (5 hours)
1 Tesla K40m  | 0.25-0.35              | ~86% at 100K steps (4 hours)

Usage:
Please see the tutorial and website for how to download the CIFAR-10
data set, compile the program and train the model.

http://tensorflow.org/tutorials/deep_cnn/
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
import os.path
import time

import pycurl
import re
from StringIO import StringIO
import tinys3
import os
import sys
import random, string
import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf
import pprint
from tensorflow.models.image.cifar10 import cifar10

interrupt_check_url = "http://169.254.169.254/latest/meta-data/spot/termination-time"

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('train_dir', '/tmp/cifar10_train',
                           """Directory where to write event logs """
                           """and checkpoint.""")
tf.app.flags.DEFINE_integer('max_steps', sys.maxint,
                            """Number of batches to run.""")
tf.app.flags.DEFINE_boolean('log_device_placement', False,
                            """Whether to log device placement.""")
tf.app.flags.DEFINE_string('checkpoint_dir', None,
                           """Checkpoint file path to start training""")


def train():
    """Train CIFAR-10 for a number of steps."""
    with tf.Graph().as_default():
        global_step = tf.Variable(0, trainable=False)

        # Get images and labels for CIFAR-10.
        images, labels = cifar10.distorted_inputs()

        # Build a Graph that computes the logits predictions from the
        # inference model.
        logits = cifar10.inference(images)

        # Calculate loss.
        loss = cifar10.loss(logits, labels)

        # Build a Graph that trains the model with one batch of examples and
        # updates the model parameters.
        train_op = cifar10.train(loss, global_step)

        # Create a saver.
        saver = tf.train.Saver(tf.all_variables())

        # Build the summary operation based on the TF collection of Summaries.
        summary_op = tf.merge_all_summaries()

        # Build an initialization operation to run below.
        init = tf.initialize_all_variables()

        # Start running operations on the Graph.
        sess = tf.Session(config=tf.ConfigProto(
            log_device_placement=FLAGS.log_device_placement))
        sess.run(init)

        if FLAGS.checkpoint_dir is not None:
            ckpt = tf.train.get_checkpoint_state(FLAGS.checkpoint_dir)
            print("checkpoint path is %s" % ckpt.model_checkpoint_path)
            tf.train.Saver().restore(sess, ckpt.model_checkpoint_path)

        # Start the queue runners.
        print("FLAGS.checkpoint_dir is %s" % FLAGS.checkpoint_dir)
        tf.train.start_queue_runners(sess=sess)
        summary_writer = tf.train.SummaryWriter(FLAGS.train_dir, sess.graph)

        cur_step = sess.run(global_step);
        print("current step is %s" % cur_step)
        interrupt_check_duration = 0.0
        elapsed_time = time.time()
        flag = 0
        for step in xrange(cur_step, FLAGS.max_steps):
            start_time = time.time()
            _, loss_value = sess.run([train_op, loss])
            duration = time.time() - start_time
            interrupt_check_duration += duration
            if (float(interrupt_check_duration) > 5.0):
                print("checking for interruption: %s", interrupt_check_duration)
                if (decision_for_migration()):
                    print("have to migrate")
                    checkpoint_path = os.path.join(FLAGS.train_dir, 'model.ckpt')
                    print("checkpoint path is %s" % checkpoint_path)
                    saver.save(sess, checkpoint_path, global_step=step)
                    random_id = generate_random_prefix()
                    start_new_instance(checkpoint_path, step, random_id)
                    upload_checkpoint_to_s3(checkpoint_path, step, "deepspotcloud-cp-bucket", random_id)
                    break
                else:
                    print("not interrupted")
                interrupt_check_duration = 0.0
            assert not np.isnan(loss_value), 'Model diverged with loss = NaN'

            if step % 10 == 0:
                num_examples_per_step = FLAGS.batch_size
                examples_per_sec = num_examples_per_step / duration
                sec_per_batch = float(duration)

                format_str = ('%s: step %d, loss = %.2f (%.1f examples/sec; %.3f '
                              'sec/batch)')
                print(format_str % (datetime.now(), step, loss_value,
                                    examples_per_sec, sec_per_batch))

            if step % 100 == 0:
                summary_str = sess.run(summary_op)
                summary_writer.add_summary(summary_str, step)

            # Save the model checkpoint periodically.
            if step % 1000 == 0 or (step + 1) == FLAGS.max_steps:
                checkpoint_path = os.path.join(FLAGS.train_dir, 'model.ckpt')
                saver.save(sess, checkpoint_path, global_step=step)
            elapsed = (int(time.time() - elapsed_time))
            if elapsed % 300 == 0 and flag == 0:
                print("uploading current status")
                uploading_current_status_to_rds(step)
                flag = 1
            elif elapsed % 300 != 0 and flag == 1:
                flag = 0


def start_new_instance(checkpoint_path, step, random_id):
    checkpoint_name = checkpoint_path.rsplit('/', 1)[1]
    ud = random_id + "-" + checkpoint_name + "-" + str(step)
    pprint.pprint((ud))
    c = pycurl.Curl()
    c.setopt(c.URL,
             'https://xxxxxxxx.execute-api.us-west-2.amazonaws.com/deploy/start-new-instance?ud=%22' + ud + '%22')
    c.perform()


def get_instance_id():
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://169.254.169.254/2016-09-02/meta-data/instance-id')
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    return body


def decision_for_migration():
    instance_id = get_instance_id()
    path = "/tmp/" + instance_id
    return (os.path.isdir(path))


def check_if_interrupted():
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, interrupt_check_url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    return bool(re.search('.*T.*Z', body))


def get_az():
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://169.254.169.254/2016-09-02/meta-data/placement/availability-zone')
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    return body


def uploading_current_status_to_rds(step):
    az = get_az()
    c_time = datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
    c = pycurl.Curl()
    c.setopt(c.URL,
             'https://xxxxxxxx.execute-api.us-west-2.amazonaws.com/deploy/upload-deeplearning-status-to-rds?az=%22' + az + '%22&step=%22' + str(
                 step) + '%22&current_time=%22' + c_time + '%22')
    c.perform()
    c.close()


def upload_checkpoint_to_s3(source_file, current_step, bucket, random_id):
    conn = tinys3.Connection(os.environ["AWS_ACCESS_KEY_ID"], os.environ["AWS_SECRET_ACCESS_KEY"], tls=True)
    upload_files = [source_file + "-" + str(current_step), source_file + "-" + str(current_step) + ".meta",
                    source_file.rsplit('/', 1)[0] + "/checkpoint"]
    pprint.pprint(random_id)
    for uf in upload_files:
        f = open(uf, 'rb')
        uploaded_name = random_id + "-" + uf.rsplit('/', 1)[1]
        print("file name: %s uploaded named: %s" % (uf, uploaded_name))
        print(type(uploaded_name))
        conn.upload(uploaded_name, f, bucket)


def generate_random_prefix(N=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


def main(argv=None):  # pylint: disable=unused-argument
    print("train directory is %s" % (FLAGS.train_dir))
    cifar10.maybe_download_and_extract()
    train()


if __name__ == '__main__':
    tf.app.run()

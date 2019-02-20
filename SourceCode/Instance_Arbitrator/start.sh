#!/bin/bash

user_data_url="http://169.254.169.254/latest/user-data"
file_location="/tmp/cifar10_train/"

train_bin_file_location="/home/ubuntu/SourceCode/tensorflow/tensorflow/models/image/cifar10/cifar10_train.py"
migration_train_bin_file_location="/home/ubuntu/SourceCode/tensorflow/tensorflow/models/image/cifar10/migration.py"

user_data=$(curl ${user_data_url})  #user_data='checkpoint-file-path:deepspotcloud-cp-bucket/EDU9SI7PAA-model.ckpt-568'
data_split=(${user_data//,/ }) # data_split = checkpoint-file-path:deepspotcloud-cp-bucket/EDU9SI7PAA-model.ckpt-568

for i in "${data_split[@]}"
do
  kv_split=(${i//:/ })
  if [[ ${kv_split[0]} == "checkpoint-file-path" ]] && [[ ${kv_split[1]} != "deepspotcloud-cp-bucket/None" ]]
  then
    checkpoint_file_path=${kv_split[1]}
  fi
done

init_cmd_train="python $train_bin_file_location --train_dir $file_location"
init_cmd_migration="python $migration_train_bin_file_location &"

if [ ${#checkpoint_file_path} -gt 0 ];
then
  init_cmd_train="$init_cmd_train --checkpoint_dir $file_location &"
  fname=${checkpoint_file_path#*/} #  fname = EDU9SI7PAA-model.ckpt-568
  id=${fname%%-*} #  id = EDU9SI7PAA
  real_name=${fname#*-} #  real_name = model.ckpt-568
  bucket_name=${checkpoint_file_path%%/*} #  bucket_name = deepspotcloud-cp-bucket
  mkdir -p ${file_location}
  aws s3 cp s3://"$checkpoint_file_path" "$file_location""$real_name" --region us-east-1
  aws s3 cp s3://"$checkpoint_file_path".meta "$file_location""$real_name".meta --region us-east-1
  aws s3 cp s3://"$bucket_name"/"$id"-checkpoint "$file_location"/checkpoint --region us-east-1
fi

echo ${init_cmd_train}
echo ${init_cmd_migration}

eval ${init_cmd_train}
eval ${init_cmd_migration}

#!/bin/bash

USER_DATA_URL="http://169.254.169.254/latest/user-data"
file_location="/tmp/cifar10_train/"
bin_file_location="/home/ubuntu/SourceCode/tensorflow/tensorflow/models/image/cifar10/cifar10_train.py"
bin_file_location1="/home/ubuntu/SourceCode/tensorflow/tensorflow/models/image/cifar10/migration.py"
user_data=$(curl $USER_DATA_URL)
data_split=(${user_data//,/ })

for i in "${data_split[@]}"
do
  kv_split=(${i//:/ })
  if [[ ${kv_split[0]} == "checkpoint-file-path" ]]
  then
    checkpoint_file_path=${kv_split[1]}
  fi
done
echo $checkpoint_file_path
init_cmd="python $bin_file_location --train_dir $file_location"
init_cmd1="python $bin_file_location1 &"
if [ ${#checkpoint_file_path} -gt 0 ];
then
  init_cmd="$init_cmd --checkpoint_dir $file_location"
  fname=${checkpoint_file_path#*/}
  id=${fname%%-*}
  real_name=${fname#*-}
  bucket_name=${checkpoint_file_path%%/*}
  mkdir -p $file_location
  aws s3 cp s3://"$checkpoint_file_path" "$file_location""$real_name" --region us-east-1
  aws s3 cp s3://"$checkpoint_file_path".meta "$file_location""$real_name".meta --region us-east-1
  aws s3 cp s3://"$bucket_name"/"$id"-checkpoint "$file_location"/checkpoint --region us-east-1
fi
init_cmd="$init_cmd &"
echo $init_cmd
eval $init_cmd
echo $init_cmd1
eval $init_cmd1
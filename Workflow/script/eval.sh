nohup python -u eval_batch.py \
    -i ../benchmark/result/202605.csv \
    -o result/Workflow_H_gpt-5-mini.csv \
    -c config/config_H_gpt-5-mini.yaml \
    &>log/eval_H_gpt-5-mini.log &

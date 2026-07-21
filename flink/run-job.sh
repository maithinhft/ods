./flink-cdc/bin/flink-cdc.sh ./jobs/cdc-mysq-to-starrocks.yml \
  -Dexecution.checkpointing.interval=60s \
  -Dexecution.checkpointing.mode=EXACTLY_ONCE \
  -Dstate.backend=hashmap \
  -Dstate.checkpoints.dir=file:///tmp/flink-checkpoints

./flink-cdc/bin/flink-cdc.sh ./jobs/cdc-postgres-to-starrocks.yml \
  -Dexecution.checkpointing.interval=60s \
  -Dexecution.checkpointing.mode=EXACTLY_ONCE \
  -Dstate.backend=hashmap \
  -Dstate.checkpoints.dir=file:///tmp/flink-checkpoints
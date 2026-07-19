# submit all in one
# ./flink-cdc/bin/flink-cdc.sh ./jobs/cdc-to-ods.yml \
#   -Dexecution.checkpointing.interval=60s \
#   -Dexecution.checkpointing.mode=EXACTLY_ONCE \
#   -Dstate.backend=hashmap \
#   -Dstate.checkpoints.dir=file:///tmp/flink-checkpoints

# submit each one
./flink-cdc/bin/flink-cdc.sh ./jobs/cdc-order-table.yml \
  -Dexecution.checkpointing.interval=60s \
  -Dexecution.checkpointing.mode=EXACTLY_ONCE \
  -Dstate.backend=hashmap \
  -Dstate.checkpoints.dir=file:///tmp/flink-checkpoints
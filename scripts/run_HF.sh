#!/bin/bash

python infer.py \
  --openai_key $OPENAI_API_KEY \
  --taxo_name wiki \
  --model gpt-4o-mini \
  --numofExamples 5 \
  --run True \
  --save_path_model_response ./results/taxo_init/ \
  --demo_path ./demos/demo_wordnet_train/ \
  --ChainofLayers False \
  --iteratively False
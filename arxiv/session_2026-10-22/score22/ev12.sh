#!/bin/bash
f=/private/tmp/claude-501/-Users-egurvanov-python-arxiv/62273097-308d-49ff-beee-038385e695c8/scratchpad/arxiv_2026-10-22_full/text/$1.txt
for p in '±|std\b|standard deviation|confidence interval|bootstrap' 'seed|[0-9] runs|three runs|five runs' 'ablat' 'contaminat|leak|memoriz' 'GPU|hours|compute|cost|latency|tokens' 'github\.com|huggingface\.co' 'limitation' 'significan|p ?<|p-value'; do echo "### $p"; grep -n -i -E "$p" "$f" | cut -c1-260 | head -${2:-15}; done

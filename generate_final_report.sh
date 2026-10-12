#!/bin/bash
cat research2/FINAL_REPORT.md | sed -e '/\[RESULTS GO HERE\]/r research2/eval_output.txt' -e '/\[RESULTS GO HERE\]/d' > research2/FINAL_REPORT_FILLED.md
mv research2/FINAL_REPORT_FILLED.md research2/FINAL_REPORT.md

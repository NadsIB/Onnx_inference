import onnxruntime_genai as og
from datetime import datetime

model = og.Model('cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4')
tokenizer = og.Tokenizer(model)


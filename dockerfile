FROM public.ecr.aws/lambda/python:3.10

# Install dependencies
RUN pip install pandas numpy scipy scikit-learn scikit-optimize

# Copy your code
COPY preprocessing/ ${LAMBDA_TASK_ROOT}/preprocessing/
COPY scoring/ ${LAMBDA_TASK_ROOT}/scoring/
COPY optimization/ ${LAMBDA_TASK_ROOT}/optimization/
COPY postprocessing/ ${LAMBDA_TASK_ROOT}/postprocessing/
COPY main.py ${LAMBDA_TASK_ROOT}/
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/

CMD ["lambda_handler.lambda_handler"]
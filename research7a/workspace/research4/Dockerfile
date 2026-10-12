FROM python:3.12.7-slim
WORKDIR /app
COPY kit.py /app/kit.py
COPY research/terminal_model.py /app/research/terminal_model.py
COPY research3/__init__.py research3/policy.py research3/model_candidates.py /app/research3/
COPY research4/__init__.py research4/policy.py research4/candidates.py /app/research4/
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 65534:65534
ENTRYPOINT ["python", "-m", "research4.policy"]

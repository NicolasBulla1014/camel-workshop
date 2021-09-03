FROM python:3.8-slim-buster
LABEL summary="Script for test camel workshop" \
      io.k8s.display-name="camel workshop tester" \
      io.openshift.tags="workshop-tester"
WORKDIR /app
COPY . .
ADD https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/4.6.4/openshift-client-linux-4.6.4.tar.gz /app
RUN pip3 install -r requirements.txt && \
    tar -xvf openshift-client-linux-4.6.4.tar.gz
ENV PATH="/app:${PATH}"
RUN chown -R 0 /app && \
    chmod -R g=u /app
EXPOSE 8080
USER 1001
CMD [ "python3", "-m" , "uvicorn", "tester:app", "--host=0.0.0.0", "--port=8080", "--timeout-keep-alive=300"]
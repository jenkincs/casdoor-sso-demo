FROM casbin/casdoor:v4.20.0
USER root
RUN apk add --no-cache python3 && mkdir -p /data && chown 1000:1000 /data
COPY casdoor/bootstrap.py /bootstrap.py
USER 1000
ENTRYPOINT ["python3", "/bootstrap.py"]

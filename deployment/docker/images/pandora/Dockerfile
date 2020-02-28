FROM python:3.8
MAINTAINER WangLy "xph_wangly10@163.com"
ENV PYTHONUNBUFFERD 1
RUN mkdir /pandora
COPY requirement.txt /pandora/
WORKDIR /pandora
RUN pip install -r requirement.txt
CMD ["/bin/bash"]
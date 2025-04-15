FROM python:3.8.18-slim
# Or any preferred Python version.
ADD botapp.py .
ADD .env .
RUN pip install -U pip
RUN pip install python-dotenv slack-sdk slack-bolt prettytable
RUN pip install pymssql
CMD ["python", "./botapp.py"] 
# Or enter the name of your unique directory and parameter set.

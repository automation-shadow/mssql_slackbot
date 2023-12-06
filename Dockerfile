FROM python:3.8.18-slim
# Or any preferred Python version.
ADD botapp.py .
ADD .env .
RUN pip install --upgrade pip
RUN pip3 install python-dotenv slack-sdk slack-bolt pymssql prettytable
CMD ["python", "./botapp.py"] 
# Or enter the name of your unique directory and parameter set.


To start server:
tox run -e run 
OR 
uvicorn app.main:app --reload

To train the model:
python venv/Lib/site-packages/career_app_model/train_model.py

Make sure Milvus server is up and running.

To create the vectorizer.joblib file:
python venv/Lib/site-packages/career_app_model/create_and_save_vectorizer.py


kill server windows
tasklist - to search task pid
taskkill /F /PID 924

create secret key
openssl rand -hex 32

create requirements.txt file
pip freeze > requirements.txt
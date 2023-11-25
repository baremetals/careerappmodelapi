
To start server:
tox run -e run

To train the model:
python venv/Lib/site-packages/career_app_model/train_model.py

Make sure Milvus server is up and running.

To create the vectorizer.joblib file:
python venv/Lib/site-packages/career_app_model/create_and_save_vectorizer.py
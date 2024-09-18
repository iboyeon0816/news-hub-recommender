from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import tensorflow as tf
tf.get_logger().setLevel('ERROR') # only show error messages

from recommenders.models.newsrec.newsrec_utils import prepare_hparams
from recommenders.models.newsrec.models.lstur import LSTURModel
from recommenders.models.newsrec.io.mind_iterator import MINDIterator

from services.news_service import NewsService
from configs.config import YAML_FILE, WORD_EMB_FILE, WORD_DICT_FILE, USER_DICT_FILE, WEIGHTS_PATH

app = Flask(__name__)

load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

news_service = NewsService(
  host=db_host,
  user=db_user,
  password=db_password,
  database=db_name
)

session = tf.compat.v1.Session()
tf.compat.v1.keras.backend.set_session(session)

hparams = prepare_hparams(YAML_FILE, 
                          wordEmb_file=WORD_EMB_FILE, 
                          wordDict_file=WORD_DICT_FILE, 
                          userDict_file=USER_DICT_FILE, 
                          batch_size=32, 
                          epochs=5)

iterator = MINDIterator
model = LSTURModel(hparams, iterator, seed=40)

try:
  model.model.load_weights(WEIGHTS_PATH)
except Exception as e:
  print(f"Error loading weights: {e}")
  exit(1)

@app.route('/recommended-news', methods=['GET'])
def recommended_news():
  user_id = request.args.get('user_id')
  if not user_id:
    return jsonify({"error": "user_id parameter is required"}), 400
  
  try:
    candidate_news = news_service.get_candidate_news(user_id)
    clicked_news = news_service.get_clicked_news(user_id)
  except Exception as e:
    return jsonify({"error": str(e)}), 500
  
  if candidate_news is None or clicked_news is None:
    return jsonify({"error": "Failed to retrieve news"}), 500

  try:
    with session.as_default():
      with session.graph.as_default():
        session.run(tf.compat.v1.global_variables_initializer()) 
        
        model.model.load_weights(WEIGHTS_PATH)
        pred = model.predict(user_id, candidate_news, clicked_news)
        
        news_with_pred = list(zip(pred, candidate_news))
        top_10_news = sorted(news_with_pred, key=lambda x: x[0], reverse=True)[:10]
        top_10_news_ids = [news[1][0] for news in top_10_news]

        return jsonify({"recommended_news_ids": top_10_news_ids})
  except Exception as e:
    return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
  
if __name__ == '__main__':
  app.run(debug=True) 
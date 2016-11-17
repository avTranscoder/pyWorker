import json

from flask import request, Response, abort, jsonify

from py_worker import app
from pyAvTranscoder import avtranscoder as av

@app.route('/ping')
def api_ping():
    return 'pong'

@app.route('/probe', methods=['GET'])
def get_probe_on_file():
    path = request.args.get('path')
    app.logger.info('Path %s', path)
    av.preloadCodecsAndFormats()
    inputFile = av.InputFile(str(path))
    data = inputFile.getProperties().asJson()
    return Response(data, mimetype='application/json')

@app.route('/jobs', methods=['GET'])
def get_all_jobs():
    jobs = {
      "jobs": [
        {
          "id": 123456
        }
      ],
      "count": 1,
      "total": 1,
      "offset": 0
    }
    return jsonify(**jobs)

@app.route('/jobs', methods=['POST'])
def post_new_job():
    input_data = json.loads(request.data)

    job = {
      "id": 123456
    }
    return jsonify(**job)

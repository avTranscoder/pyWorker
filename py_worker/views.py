import os
import json

from flask import request, Response, abort, jsonify, send_file

from py_worker import app
from pyAvTranscoder import avtranscoder as av

# av.Logger().setLogLevel(av.AV_LOG_QUIET)

@app.route('/ping')
def api_ping():
    return jsonify({'ping': 'pong'})

@app.route('/')
def index():
    libs = av.getLibraries()
    libraries = []
    for library in av.getLibraries():
        libraries.append({
            'name': library.getName(),
            'version': library.getStringVersion(),
            'licence': library.getLicense(),
            })

    av.preloadCodecsAndFormats();
    inputExtensions = []
    for extension in av.getInputExtensions():
        inputExtensions.append(extension)
    outputExtensions = []
    for extension in av.getOutputExtensions():
        outputExtensions.append(extension)

    infos = {
        "libraries": libraries,
        "inputExtensions": inputExtensions,
        "outputExtensions": outputExtensions,
    }
    return jsonify(**infos)


@app.route('/ui')
def small_ui():
    return send_file(os.path.join("interface", "index.html"))

@app.route('/probe', methods=['GET'])
def get_probe_on_file():
    path = request.args.get('path')

    if path == None:
        abort(400)

    level = request.args.get('level', 'fast')

    analyse_gop_state = "disabled"
    if level == 'firstGop':
        analyse_gop_state = "enabled"

    app.logger.info('Analyse path: %s - GOP analysis: %s', path, analyse_gop_state)
    av.preloadCodecsAndFormats()
    inputFile = av.InputFile(str(path))
    if level == 'firstGop':
        inputFile.analyse(av.NoDisplayProgress(), av.eAnalyseLevelFirstGop)
    data = inputFile.getProperties().allPropertiesAsJson()

    response = Response(data, mimetype='application/json')
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route('/thumbnail', methods=['GET'])
def get_thumbnail_on_file():
    path = request.args.get('path')
    frame = float(request.args.get('frame', 0))

    if path == None:
        abort(400)

    analyse_gop = request.args.get('analyse_gop', False)

    analyse_gop_state = "disabled"
    if analyse_gop:
        analyse_gop_state = "enabled"

    app.logger.info('Analyse path: %s - GOP analysis: %s', path, analyse_gop_state)
    av.preloadCodecsAndFormats()
    inputFile = av.InputFile(str(path))

    # inputFile.seekAtFrame(frame, av.AVSEEK_FLAG_FRAME)
    # inputFile.seekAtFrame(frame, av.AVSEEK_FLAG_ANY)
    # inputFile.seekAtFrame(frame, av.AVSEEK_FLAG_BACKWARD)

    tmpFilename = "/tmp/thumbnails.jpg"

    # create output file (need to set format profile of encoding to force output format to mjpeg)
    formatProfile = av.ProfileMap()
    formatProfile[av.avProfileIdentificator] = "thumbnailFormatPreset"
    formatProfile[av.avProfileIdentificatorHuman] = "Thumbnail format preset"
    formatProfile[av.avProfileType] = av.avProfileTypeFormat
    formatProfile[av.avProfileFormat] = "mjpeg"
    outputFile = av.OutputFile(tmpFilename)
    outputFile.setupWrapping(formatProfile)

    # create input stream
    videoProperties = inputFile.getProperties().getVideoProperties()[0]
    videoStreamIndex = videoProperties.getStreamIndex()
    videoWidth = videoProperties.getWidth()
    videoHeight = videoProperties.getHeight()
    videoFps = videoProperties.getFps()
    dar = videoProperties.getDar()

    # inputStream = av.InputStream(inputFile, videoStreamIndex)
    # inputStream.activate()

    inputStreamDesc = av.InputStreamDesc(str(path), videoStreamIndex)

    # create output stream
    videoProfile = av.ProfileMap()
    videoProfile[av.avProfileIdentificator] = "thumbnailVideoPreset"
    videoProfile[av.avProfileIdentificatorHuman] = "Thumbnail video preset"
    videoProfile[av.avProfileType] = av.avProfileTypeVideo
    videoProfile[av.avProfileCodec] = "mjpeg"
    # videoProfile[av.avProfilePixelFormat] = "yuvj420p"
    videoProfile[av.avProfilePixelFormat] = "yuvj422p"
    if 'width' in request.args:
        videoProfile[av.avProfileWidth] = str(request.args["width"])
        videoProfile[av.avProfileHeight] = str(videoHeight*int(request.args["width"])/videoWidth)
    # if 'height' in request.args:
    #     videoProfile[av.avProfileHeight] = str(request.args["height"])

    # create transcoder
    transcoder = av.Transcoder(outputFile)
    transcoder.addStream(inputStreamDesc, videoProfile, -frame/25)

    # launch process
    outputFile.beginWrap()
    transcoder.preProcessCodecLatency()
    transcoder.processFrame()
    outputFile.endWrap()

    return send_file(tmpFilename, mimetype='image/gif')

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

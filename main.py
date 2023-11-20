from flask import Flask, request
from googleapiclient import discovery

API_KEY = 'AIzaSyC8JIK1zTTVzjP8-2GDGu5lWmAGmMhqJwQ'
API_URL = "https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1"

app = Flask(__name__)

# Function to predict tone based on the sentence


def predict_tone(sentence):
    # Creates the client
    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl=API_URL,
        static_discovery=False,
    )

    # Analyze the sentence using Perspective API
    analyze_request = {
        'comment': {'text': sentence},
        'requestedAttributes': {
            'TOXICITY': {},
            'PROFANITY': {},
            'FLIRTATION': {}
        }
    }

    # Get the response
    response = client.comments().analyze(body=analyze_request).execute()

    # Get the scores for different aspects
    toxicity_score = response['attributeScores']['TOXICITY']['summaryScore']['value']
    flirtation_score = response['attributeScores']['FLIRTATION']['summaryScore']['value']
    profanity_score = response['attributeScores']['PROFANITY']['summaryScore']['value']

    # Determine the tone based on the scores
    if toxicity_score > 0.7 or profanity_score > 0.7:
        return "Highly Offensive"
    elif toxicity_score > 0.5 or profanity_score > 0.5:
        return "Moderately Offensive"
    elif flirtation_score > 0.7:
        return "Very Friendly"
    elif flirtation_score > 0.5:
        return "Friendly"
    else:
        return "Neutral/Professional"


@app.route('/', methods=['POST'])
def slack_command():
    # Data object from Slack
    data = request.form

    # Example sentence from a Slack slash command object
    input_sentence = data.get('text')

    # Predict the tone of the sentence
    predicted_tone = predict_tone(input_sentence)

    # Slack formatted response
    res = {
        "response_type": "ephemeral",
        "text": predicted_tone + ' - Sentence: ' + input_sentence
    }

    return res


if __name__ == '__main__':
    app.run(debug=True)

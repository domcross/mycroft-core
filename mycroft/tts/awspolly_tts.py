# Copyright 2020 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import boto3

from mycroft.tts import TTS, TTSValidator
from mycroft.configuration import Configuration


class AWSPollyTTS(TTS):
    def __init__(self, lang, config):
        super(AWSPollyTTS, self).__init__(lang, config, AWSPollyTTSValidator(self), 'mp3')
        self.config = Configuration.get().get("tts", {}).get("awspolly", {})
        self.aws_access_key_id = self.config.get('aws_access_key_id', None)
        self.aws_secret_access_key = self.config.get('aws_secret_access_key', None)
        self.region_name = self.config.get('region_name', 'us-east-1')  # change to other region for better latency
        self.voice_id = self.config.get('VoiceID', 'Matthew')  # VoiceId determines the language

    def get_tts(self, sentence, wav_file):
        polly_client = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name).client('polly')
        response = polly_client.synthesize_speech(VoiceId=self.voice_id,
                OutputFormat='mp3',
                Text=sentence)
        file = open(wav_file, 'wb')
        file.write(response['AudioStream'].read())
        file.close()

        return (wav_file, None)  # No phonemes


class AWSPollyTTSValidator(TTSValidator):
    def __init__(self, tts):
        super(AWSPollyTTSValidator, self).__init__(tts)

    def validate_lang(self):
        # TODO
        pass

    def validate_connection(self):
        config = Configuration.get().get("tts", {}).get("awspolly", {})
        aws_access_key_id = config.get('aws_access_key_id', None)
        aws_secret_access_key = config.get('aws_secret_access_key', None)
        region_name = config.get('region_name', 'us-east-1')
        if not aws_access_key_id or not aws_secret_access_key:
            raise Exception(
                'AWS Access key and/or secret missing in configuration')

        try:
            polly_client = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name).client('polly')
        except Exception:
            raise Exception(
                'AWSPollyTTS server could not be verified. Please check your '
                'internet connection.')

    def get_tts_class(self):
        return AWSPollyTTS

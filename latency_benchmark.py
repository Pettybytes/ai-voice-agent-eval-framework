"""Opt-in ElevenLabs transport benchmark. Bytes received are not audio played."""
import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from metrics import distribution, number


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('TTS redirects are not allowed')


def measure_tts_latency(text, api_key, voice_id, model_id='eleven_flash_v2_5',
                        timeout_s=20, max_audio_bytes=20_000_000, opener=None, clock=time.perf_counter):
    """First audio byte and full body receipt in ms, on a monotonic clock.

    Reads one byte first to avoid timing a 1 KB buffer fill. Does not decode or
    play audio. Timeout is socket inactivity plus elapsed checks between reads;
    a blocked read can overrun the elapsed budget by timeout_s.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError('text is required')
    if not api_key or api_key in {'test_key', 'your_key_here'}:
        raise ValueError('set ELEVENLABS_API_KEY')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', voice_id or '') or voice_id in {'voice_id', 'your_voice_id'}:
        raise ValueError('set an actual ELEVENLABS_VOICE_ID')
    if not model_id:
        raise ValueError('model_id is required')
    number(timeout_s, 'timeout_s', 0.001)
    number(max_audio_bytes, 'max_audio_bytes', 1)
    request = urllib.request.Request(
        f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream?output_format=mp3_44100_128',
        data=json.dumps({'text': text, 'model_id': model_id}).encode(),
        headers={'xi-api-key': api_key, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'}, method='POST')
    opener = opener or urllib.request.build_opener(NoRedirect())
    started = clock()
    try:
        with opener.open(request, timeout=timeout_s) as response:
            if response.status != 200:
                raise ValueError(f'TTS returned HTTP {response.status}')
            content_type = response.headers.get('Content-Type', '').split(';', 1)[0].lower()
            if not (content_type.startswith('audio/') or content_type == 'application/octet-stream'):
                raise ValueError('TTS did not return an audio content type')
            first = response.read(1)
            first_at = clock()
            if not first:
                raise ValueError('TTS returned an empty audio stream')
            size = len(first)
            while True:
                if clock() - started > timeout_s:
                    raise TimeoutError('TTS elapsed-time budget exceeded')
                chunk = response.read(4096)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_audio_bytes:
                    raise ValueError('TTS response exceeds audio size limit')
            finished = clock()
    except urllib.error.HTTPError as exc:
        exc.close()
        raise ValueError(f'TTS returned HTTP {exc.code}') from None
    except (urllib.error.URLError, OSError):
        raise ValueError('TTS transport failed or timed out') from None
    return {'first_audio_byte_ms': (first_at - started) * 1000,
            'stream_complete_ms': (finished - started) * 1000, 'audio_bytes': size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='authorize billable provider requests')
    parser.add_argument('--text', default='Hello. How can I help you today?')
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--model-id', default='eleven_flash_v2_5')
    args = parser.parse_args()
    if not args.live or not 1 <= args.runs <= 100:
        parser.error('--live and 1..100 runs are required')
    try:
        samples = [measure_tts_latency(args.text, os.getenv('ELEVENLABS_API_KEY'),
                                      os.getenv('ELEVENLABS_VOICE_ID'), args.model_id) for _ in range(args.runs)]
    except ValueError as exc:
        parser.exit(2, f'{exc}\n')
    print(json.dumps({'source': 'live', 'model_id': args.model_id, 'samples': samples,
                      'first_audio_byte_ms': distribution([s['first_audio_byte_ms'] for s in samples])}, indent=2))


if __name__ == '__main__':
    main()

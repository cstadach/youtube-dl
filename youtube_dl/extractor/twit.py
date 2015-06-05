from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    determine_ext,
    int_or_none,
    parse_duration,
    unified_strdate,
)


class TwitIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?twit\.tv/shows/(?P<show>[^/]+)/episodes/(?P<number>\d+)'

    _TESTS = [
        {
            'url': 'http://www.twit.tv/tnt/1265',
            'md5': '79737e740a671a93c8daf12f405c3824',
            'info_dict': {
                'id': 'tnt1265',
                'ext': 'mp4',
                'title': 'Tech News Today 1265',
                'description': 'md5:c5f7a68a31e389a09b2e7bb2f6fa4777',
                'upload_date': '20150522',
                'duration': 2237,
            },
        },
        {
            'url': 'http://www.twit.tv/shows/security-now/episodes/500',
            'md5': '62d77437d5ad357cbb3e3982afe35be4',
            'info_dict': {
                'id': 'sn0500',
                'ext': 'mp4',
                'title': 'Security Now 500',
                'description': 'md5:b2987ae3c1ce0ab3a3622e1279f012d2',
                'upload_date': '20150324',
                'duration': 5981,
            },
        },
    ]

    def _real_extract(self, url):
        mobj = re.search(self._VALID_URL, url)
        display_id = '_'.join(mobj.groups())
        webpage = self._download_webpage(url, display_id)
        title = self._og_search_title(webpage).split(' | ')[0]

        download_options = self._search_regex(
            r'(?s)<div class="choices[^"]+"[^>]*>(.*?)</div>',
            webpage, 'download options')
        urls_info = re.findall(
            '<a href\s*=\s*"(?P<url>[^"]+)"[^>]*>(?P<id>[^<]*)</a>',
            download_options)
        formats = []
        video_id = None
        for url, format_info in urls_info:
            format_id = format_info.replace(' ', '-')
            ext = determine_ext(url)
            width = height = bitrate = None

            if ext == 'mp4':
                format_mobj = re.search(
                    '.*/(?P<id>[^_./]+)(?:_[^_]+_(?P<width>\d*)x(?P<height>\d*)_(?P<bitrate>\d*))?\.', url)
                if format_mobj:
                    width = int_or_none(format_mobj.group('width'))
                    height = int_or_none(format_mobj.group('height'))
                    bitrate = int_or_none(format_mobj.group('bitrate'))
                    video_id = format_mobj.group('id')
            formats.append({
                'format_id': format_id,
                'url': url,
                'width': width,
                'height': height,
                'tbr': bitrate,
            })
        self._sort_formats(formats)

        upload_date = unified_strdate(self._search_regex(
            r'<p[^>]*class="air-date"[^>]*>([^<]*)</p>',
            webpage, 'upload date', default=None, fatal=False))
        duration = parse_duration(self._search_regex(
            r'Running time:(?:</strong>)?\s*((?:\d{,2}:){,2}\d{2})',
            webpage, 'duration', default=None, fatal=False))

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'description': self._og_search_description(webpage),
            'thumbnail': self._og_search_thumbnail(webpage),
            'upload_date': upload_date,
            'duration': duration,
        }

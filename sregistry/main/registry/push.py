'''

push.py: push functions for sregistry client

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from sregistry.logger import bot, ProgressBar
from sregistry.utils import (
    parse_image_name,
    parse_header,
    remove_uri
)
from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

import requests
import json
import sys
import os


def push(self, path, name, tag=None):
    '''push an image to Singularity Registry'''

    path = os.path.abspath(path)
    image = os.path.basename(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.error('%s does not exist.' %path)
        sys.exit(1)

    # Interaction with a registry requires secrets
    self.require_secrets()

    # Extract the metadata
    names = parse_image_name(remove_uri(name), tag=tag)
    metadata = self.get_metadata(path, names=names) or {}

    # Add expected attributes
    if "data" not in metadata:
        metadata['data'] = {'attributes': {}}
    if "labels" not in metadata['data']['attributes']:
        metadata['data']['attributes']['labels'] = {}
    if metadata['data']['attributes']['labels'] == None:
        metadata['data']['attributes']['labels'] = {}

    # Try to add the size
    image_size = os.path.getsize(path) >> 20
    fromimage = os.path.basename(path)
    metadata['data']['attributes']['labels']['SREGISTRY_SIZE_MB'] = image_size
    metadata['data']['attributes']['labels']['SREGISTRY_FROM'] = fromimage

    # Prepare push request with multipart encoder
    url = '%s/push/' % self.base
    upload_to = os.path.basename(names['storage'])

    SREGISTRY_EVENT = self.authorize(request_type="push",
                                     names=names)

    encoder = MultipartEncoder(fields={'collection': names['collection'],
                                       'name':names['image'],
                                       'metadata': json.dumps(metadata),
                                       'tag': names['tag'],
                                       'datafile': (upload_to, open(path, 'rb'), 'text/plain')})

    progress_callback = create_callback(encoder)
    monitor = MultipartEncoderMonitor(encoder, progress_callback)
    headers = {'Content-Type': monitor.content_type,
               'Authorization': SREGISTRY_EVENT }

    try:
        r = requests.post(url, data=monitor, headers=headers)
        message = self._read_response(r)

        print('\n[Return status {0} {1}]'.format(r.status_code, message))

    except KeyboardInterrupt:
        print('\nUpload cancelled.')





/api/containers/upload-complete/	shub.apps.api.actions.upload.ShubChunkedUploadCompleteView	api_chunked_upload_complete
/api/containers/upload/	shub.apps.api.actions.upload.ShubChunkedUploadView	api_chunked_upload





 <script type="text/javascript">
    var md5 = "",
        csrf = $("input[name='csrfmiddlewaretoken']")[0].value,
        form_data = [{"name": "csrfmiddlewaretoken", "value": csrf}];
    function calculate_md5(file, chunk_size) {
      var slice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice,
          chunks = chunks = Math.ceil(file.size / chunk_size),
          current_chunk = 0,
          spark = new SparkMD5.ArrayBuffer();
      function onload(e) {
        spark.append(e.target.result);  // append chunk
        current_chunk++;
        if (current_chunk < chunks) {
          read_next_chunk();
        } else {
          md5 = spark.end();
        }
      };
      function read_next_chunk() {
        var reader = new FileReader();
        reader.onload = onload;
        var start = current_chunk * chunk_size,
            end = Math.min(start + chunk_size, file.size);
        reader.readAsArrayBuffer(slice.call(file, start, end));
      };
      read_next_chunk();
    }
    $("#chunked_upload").fileupload({
      url: "{% url 'api_chunked_upload' %}",
      dataType: "json",
      maxChunkSize: 100000, // Chunks of 100 kB
      formData: form_data,
      add: function(e, data) { // Called before starting upload
        $("#messages").empty();
        // If this is the second file you're uploading we need to remove the
        // old upload_id and just keep the csrftoken (which is always first).
        form_data.splice(1);
        calculate_md5(data.files[0], 100000);  // Again, chunks of 100 kB
        data.submit();
      },
      chunkdone: function (e, data) { // Called after uploading each chunk
        if (form_data.length < 2) {
          form_data.push(
            {"name": "upload_id", "value": data.result.upload_id}
          );
        }
        $("#messages").append($('<p>').text(JSON.stringify(data.result)));
        var progress = parseInt(data.loaded / data.total * 100.0, 10);
        $("#progress").text(Array(progress).join("=") + "> " + progress + "%");
      },
      done: function (e, data) { // Called when the file has completely uploaded
        $.ajax({
          type: "POST",
          url: "{% url 'api_chunked_upload_complete' %}",
          data: {
            csrfmiddlewaretoken: csrf,
            upload_id: data.result.upload_id,
            md5: md5
          },
          dataType: "json",
          success: function(data) {
            $("#messages").append($('<p>').text(JSON.stringify(data)));
          }
        });
      },
    });
  </script>

</body>
</html>









def create_callback(encoder):
    print(encoder)
    encoder_len = encoder.len / (1024*1024.0)
    bar = ProgressBar(expected_size=encoder_len,
                      filled_char='=')
    def callback(monitor):
        print(monitor)
        bar.show(monitor.bytes_read / (1024*1024.0))
    return callback

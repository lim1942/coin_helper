from rest_framework.views import APIView
from rest_framework.response import Response
from coin_spider import serializers
from coin_db import get_db_by_channel_source
from django.http import StreamingHttpResponse


class DataExportView(APIView):

    def get_serializer(self, *args, **kwargs):
        return serializers.DataExportSerializer(*args,**kwargs)

    def get(self,request,*args,**kwargs):
        return Response("数据导出接口")

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel = serializer.data['channel']
        instrument_id = serializer.data['instrument_id']
        crypto_margined = serializer.data['crypto_margined']
        if channel.endswith('swap') and crypto_margined:
            instrument_id = instrument_id.replace('-USDT','-USD')
        start = serializer.data['start']
        end = serializer.data['end']
        source = serializer.data['source']
        db = get_db_by_channel_source(channel,source,instrument_id)
        try:
            result = db.query_csv(instrument_id,start,end)
            resp = StreamingHttpResponse(result)
            start_str = start.strftime('%Y%m%d%H%M%S')
            end_str = end.strftime('%Y%m%d%H%M%S')
            resp["Content-Disposition"] = f'attachment; filename={"_".join([channel,instrument_id,start_str,end_str])}.csv'
            resp["Access-Control-Expose-Headers"] = "Content-Disposition"
            return resp
        except Exception as e:
            return Response({'error':str(e)})
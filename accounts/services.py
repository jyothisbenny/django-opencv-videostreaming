def create_update_record(request, serializer_class, model_class):
    request_data = request.data.copy() if not isinstance(request, dict) else request
    data_id = request_data.pop('id', None)
    if data_id:
        data_obj = model_class.objects.get(id=data_id)
        serializer = serializer_class(instance=data_obj, data=request_data, partial=True,
                                      context={"request": request})
    else:
        serializer = serializer_class(data=request_data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    update_object = serializer.save()
    return serializer_class(instance=update_object).data

from django.shortcuts import render
from django.contrib import messages
from pylovepdf.ilovepdf import ILovePdf
import os,shutil
from django.conf import settings
from django.http import HttpResponse, Http404

from PlayPDF.forms import UploadFileForm
from PlayPDF.models import UploadedFile


def merge_pdfs(request):
    status_message = 'please upload a file'
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            list_of_files = upload_files(request)
            output_filename = merge_files(list_of_files)
            output_file = download_file('output\\' + output_filename)
            shutil.rmtree('media')
            messages.success(request, "Data merged successfully")
            status_message = 'Uploaded files are merged successfully and downloaded '
            return output_file
    else:
        messages.warning(request,"Upload files")
        form = UploadFileForm()

    return render(request, 'merge_pdf.html', {'form': form, 'status_message':status_message})


def upload_files(request):
    list_of_files = []
    for uploaded_file in request.FILES.getlist('files'):
        # task.add_file(uploaded_file.read())
        list_of_files.append('media/uploads/' + (uploaded_file.name.replace(' ', '_')))
        UploadedFile.objects.create(file=uploaded_file)
    return list_of_files


def merge_files(list_of_files):
    public_key = 'project_public_57e7715c23c8350433dcb28a3f09f8d2_HYwC2ac7ab811c06011aba6ecdb63df5e2613'
    ilovepdf = ILovePdf(public_key, verify_ssl=True)
    # assigning a new compress task
    task = ilovepdf.new_task('merge')
    # adding the pdf file to the task
    # setting the output folder directory
    # if no folder exist it will create one
    task.set_output_folder('media/output')
    # delete the task
    task.delete_current_task()
    # add files to the task
    for file_path in list_of_files:
        task.add_file(file_path)
    # execute the task
    task.execute()
    # download the task
    output_filename = task.download()
    task.delete_current_task()
    return output_filename


def download_file(path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

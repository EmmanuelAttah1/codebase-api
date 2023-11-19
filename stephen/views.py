from django.db.models import Q

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .utils import getChunkDependency,generate_doc
from .models import Project,FileChunk,ProjectFile
from .serializer import ChunkSeializer, UserLoginSerializer

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import permissions

# Create your views here.

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow any user to access this view.

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            # print("my errors are ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
def createNewProject(request):
    name = request.POST['name']

    try:
        project  = Project.objects.get(name=name)

    except Project.DoesNotExist:
        project = Project(name=name)
        project.save()

    return Response({'msg':"done"})

@api_view(['POST'])
def generateChunkDoc(request):
    data = request.POST

    # print(data)

    chunk = data['chunk']
    file_name = data['file']
    chunkName = data['name']
    dependencies = data['dependencies']
    chunk_range = data['range']
    project = data['project']
    context = data['docContext']

    #get project file
    # print("my project is ",project)

    # try:
    project  = Project.objects.get(name=project)

    # except Project.DoesNotExist:
    #     project = Project(name=project)
    #     project.save()

    chunk_dependency = ""

    if len(dependencies) != 0:
        chunk_dependency = getChunkDependency(dependencies,file_name,chunkName=="head")

    doc = generate_doc(chunk, chunk_dependency,context)

    try:
        file = ProjectFile.objects.get(Q(name=file_name)&Q(project=project))

    except ProjectFile.DoesNotExist:
        file = ProjectFile()
        file.name = file_name
        file.project = project
        file.save()

    # save doc
    try:
        doc_chunk = FileChunk.objects.get(
            Q(file=file)&Q(chunk=chunk)
        )
    except FileChunk.DoesNotExist:
        doc_chunk = FileChunk(file=file,chunk=chunk,name=chunkName,chunk_range=chunk_range)

    doc_chunk.doc = doc
    doc_chunk.save()


    return Response({"status":"done"})

@api_view(['GET'])
def getFileDoc(request,file_name,project_name):
    # try:
    project = Project.objects.get(name=project_name)
    doc_file = ProjectFile.objects.get(Q(name=file_name)&Q(project=project))
    chunks = FileChunk.objects.filter(file=doc_file)

    return Response({
        'data':ChunkSeializer(chunks,many=True).data
    })
    # except:
    #     return Response({
    #         'data':[]
    #     })

@api_view(['POST'])
def updateFile(request):
    data = request.POST
    project = data['project']
    old_name = data['old_name']
    new_name = data['new_name']

    try:
        project = Project.objects.get(name=project)
        file = ProjectFile.objects.get(
            Q(name=old_name)
            &Q(project=project)
        )

        file.name = new_name
        file.save()

    except Project.DoesNotExist:
        pass
    except ProjectFile.DoesNotExist:
        pass

    return Response({'msg':"done"})


@api_view(['POST'])
def editChunkDoc(request):
    data = request.POST
    project = data['project']
    projectFile = data['file']
    name = data['name']
    doc = data['doc']

    try:
        project = Project.objects.get(name=project)
        file = ProjectFile.objects.get(name=projectFile)
        chunk = FileChunk.objects.get(
            Q(name=name)
            &Q(file=file)
        )

        if (len(doc) > 0):
            chunk.doc = doc
            chunk.save()

    except FileChunk.DoesNotExist:
        pass
    except ProjectFile.DoesNotExist:
        pass
    except Project.DoesNotExist:
        pass

    return Response({"msg":"done"})

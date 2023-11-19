from django.db.models import Q

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .utils import generate_doc
from .models import Project,FileChunk,ProjectFile
from .serializer import ChunkSeializer, UserLoginSerializer

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import permissions

import asyncio
import aiohttp
import json
from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import process_chunk, count_token

from mycodebase.settings import OPEN_AI_MAX_TOKEN


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


class GenerateChunkDoc(APIView):

    async def process_chunks(self, chunks):
        async with aiohttp.ClientSession() as session:
            tasks = []
            section = ""
            section_count = 0

            for code_chunk in chunks:
                chunk = code_chunk['chunk']
                chunk_dependency = code_chunk['chunk_dependency']
                context = code_chunk['context']
                name = code_chunk['name']

                chunk_text = process_chunk(chunk,chunk_dependency,context,name)
                chunk_count = count_token(chunk_text)

                if chunk_count + section_count > OPEN_AI_MAX_TOKEN:

                    #process chunk
                    task = asyncio.ensure_future(generate_doc(section))
                    tasks.append(task)

                    section = ""
                    section_count = 0

                section += chunk_text
                section_count += chunk_count

            if len(section) > 0:
                task = asyncio.ensure_future(generate_doc(section))
                tasks.append(task)

            # Gather all tasks to wait for their completion
            results = await asyncio.gather(*tasks, return_exceptions=True)

            return results


    def post(self,request,*args,**kwargs):
        chunk_info = {}

        # try:
        data = request.POST

        code_chunks = data['chunks']
        project = data['project']
        file_name = data['file']

        code_chunks = json.loads(code_chunks)

        for chunk in code_chunks:
            chunk_info[chunk['name']] = chunk


        project  = Project.objects.get(name=project)

        try:
            file = ProjectFile.objects.get(Q(name=file_name)&Q(project=project))

        except ProjectFile.DoesNotExist:
            file = ProjectFile()
            file.name = file_name
            file.project = project
            file.save()


        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(self.process_chunks(code_chunks))
        loop.close()


        for section in results:
            section = json.loads(section)
            for chunkData in section:
                name = chunkData['chunk_name']
                doc = chunkData['chunk_doc']

                chunk = chunk_info[name]['chunk']
                chunk_range = chunk_info[name]['range']

                # save doc
                try:
                    doc_chunk = FileChunk.objects.get(
                        Q(file=file)&Q(chunk=chunk)
                    )
                except FileChunk.DoesNotExist:
                    doc_chunk = FileChunk(file=file,chunk=chunk,name=name,chunk_range=chunk_range)

                doc_chunk.doc = doc
                doc_chunk.save()


        return Response({"status":"done"})
        
        # except Exception as e:
        #     # Handle exceptions accordingly
        #     return Response({'error': str(e)}, status=500)
        

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

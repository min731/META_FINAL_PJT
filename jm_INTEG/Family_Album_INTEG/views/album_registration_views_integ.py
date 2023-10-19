from flask import Blueprint
from flask import request
from Family_Album_INTEG.models.images_analysis.image_processor import Image_Processor
from PIL import Image
import pickle
import re
import googletrans

bp = Blueprint('album_registration_integ',__name__,url_prefix='/album_registration_integ')

# 1. 메타데이터 추출 - Python 코드
# 2. 인물 추출 - Face Recognition
# 3. 배경/물체 추출 - LLaVa
# 4. 요약 문장 생성 - LLaVa

 # 이미지 분석 객체
image_processor = Image_Processor()

# 번역 객체
translator = googletrans.Translator()

save_root_family = 'data(Family_Album)/family/'
save_root_db = 'data(Family_Album)/db/'

album_registration_db = {}
with open(save_root_db+'album_registration_db.pickle', 'rb') as f:
    album_registration_db = pickle.load(f)
face_registration_db = {}
with open(save_root_db+'/face_registration_db.pickle', 'rb') as f:
    face_registration_db = pickle.load(f)

@bp.route('/images_analysis',methods=['GET','POST'])
def images_preprocessing():

    if request.method=='POST':

        family_id = request.form['family_id']
        # print('family_id : ',family_id)
        album_registration_db[family_id] = []

        files = request.files.getlist("image")
        miss_cnt = 0

        for idx,file in enumerate(files):
            
            print("------------------ ",idx+1," ------------------")
            
            tokenizer, model, llava_image_processor, context_len,image_aspect_ratio,roles,conv,temperature,max_new_tokens,debug = image_processor.load_llava_model()

            file_data = {}

            file_data = image_processor.get_metadata(file)
            file_data = image_processor.face_recognition(file_data,file,face_registration_db[family_id])

            inference_outputs = image_processor.llava_inference_image(
                    tokenizer,
                    model,
                    llava_image_processor,
                    context_len,
                    image_aspect_ratio,
                    roles,
                    conv,
                    temperature,
                    max_new_tokens,
                    debug,
                    file)
            
            # print(" before re")
            # print(" tags :",inference_outputs[0])
            # print(" summary :",inference_outputs[1])
            
            # print(" inference_outputs : ", inference_outputs[1:])
            tags = re.sub("Places|Place|People|</s>|\\n|:|1. |\.|,,|, ,","",inference_outputs[0])
            tags = re.sub(r':','',tags)
            tags = re.sub("2.|3.|4.|5.|6.|7.|8.|9.|10.|11.|12.|13.|14.|15.|Backgrounds|Objects|Background|Object",",",tags)

            summary = re.sub("summary|</s>|\\n:","",inference_outputs[1])

            # print(" before transflation")
            # print(" tags :",tags)
            # print(" summary :",summary)

            tags = translator.translate(tags,dest='ko',src='en').text
            summary = translator.translate(summary,dest='ko',src='en').text

            tags = re.sub(" ","",tags)

            # print(" after transflation")
            # print(" tags :",tags)
            # print(" summary :",summary)

            tags = list(set(tags.split(",")))

            # print(" to list")
            # print(" tags :",tags)
            # print(" summary :",summary)

            file_data['tags']=tags
            file_data['summary']=summary

            album_registration_db[family_id].append(file_data)

            print(file.filename)
            save_name = save_root_family+file.filename.split(".")[0]+f'_{file_data["character"]}.jpg'

            if str(file_data["character"])=='[]':
                miss_cnt += 1
                
            # print("save name : ",save_name)
            save_file = Image.open(file)
            save_file.save(save_name)

        with open(save_root_db+'album_registration_db.pickle', 'wb') as f:
            pickle.dump(album_registration_db,f)

        print("miss_cnt : ",miss_cnt)
        print(album_registration_db)
        return 'Complete Album Registration (POST)'
    
    elif request.method=='GET':

        return 'Complete Album Registration (GET)'
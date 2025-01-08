'use client'

import React, {useEffect, useState} from 'react';


function upload(){
    const [state, setState] = useState();
    const [file, setFile] = useState<File | undefined>();
    const [prediction, setPrediction] = useState<Number>();
    const [certainty, setCertainty] = useState<Number>();
    const [imgURL, setImgURL] = useState<string>();
    const [preview, setPreview] = useState<string | ArrayBuffer | null>();

    async function handleOnSubmit(e: React.SyntheticEvent){
        e.preventDefault();

        if (typeof file === 'undefined') return;

        console.log('file', file)

        const formData = new FormData();

        formData.append('file', file);
        

        const results = await fetch('http://localhost:8000/upload',{
            method: 'POST',
            body: formData,
        }).then(r => r.json());
        console.log('results', results)
        setPrediction(results[0]);
        setCertainty(results[1])

        const fetchImage = await fetch(`http://localhost:8000/get/${file.name}`,{
            method: 'GET',
        });
        const imageBlob = await fetchImage.blob();
        const url = URL.createObjectURL(imageBlob)

        setImgURL(url)


        const delResult = await fetch(`http://localhost:8000/delete/${file.name}`,{
            method: 'DELETE',
        }).then(r => r.json());
        console.log('results', delResult)

        //console.log(prediction, certainty)


        

        //setState('sent');

    }

    async function handleOnChange(e: React.FormEvent<HTMLInputElement>) {
        const target = e.target as HTMLInputElement & {
            files: FileList;
        }
        setFile(target.files[0]);

        const previewFile = new FileReader;

        previewFile.onload = function() {
            setPreview(previewFile.result)
        }

        previewFile.readAsDataURL(target.files[0]);
    }


    return(
        <div>
            <form onSubmit={handleOnSubmit}>
                <input type="file" 
                name="image" 
                onChange={handleOnChange} 
                accept='image/jpeg, image/png'/>
                <img src={preview} />

                <button>Submit</button>
            </form>
            <img src={imgURL} />
        </div>
    )
}


export default upload;
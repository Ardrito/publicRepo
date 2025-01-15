'use client'

import React, {useEffect, useState} from 'react';
import {
  Card,
  Button,
  Typography,
} from "@material-tailwind/react";
import {useParams, useRouter, useSearchParams} from 'next/navigation';
import Router, {withRouter} from 'next/router'


function upload(){
    const [displayForm, setDisplayForm] = useState(true)
    const [displayReturn, setDisplayReturn] = useState(false)
    const [state, setState] = useState("Ready");
    const [file, setFile] = useState<File | undefined>();
    const [prediction, setPrediction] = useState<Number>();
    const [certainty, setCertainty] = useState<Number>();
    const [imgURL, setImgURL] = useState<string>();
    const [preview, setPreview] = useState<string | ArrayBuffer | null>();
    const [label, setLabel] = useState<Number>(11);
    let navigate = useRouter();
    const base = 'http://localhost:8001/'

    async function handleOnSubmit(e: React.SyntheticEvent){
        e.preventDefault();
        
        
        if (typeof file === 'undefined') return;

        console.log('file', file)

        const formData = new FormData();

        formData.append('file', file);
        formData.append('label', `${label}`);
        

        const results = await fetch(`${base}test`,{
            method: 'POST',
            body: formData,
        }).then(r => r.json());
        console.log('results', results)
        setPrediction(results[0]);
        setCertainty(results[1])

        const fetchImage = await fetch(`${base}get/${file.name}`,{
            method: 'GET',
        });
        const imageBlob = await fetchImage.blob();
        const url = URL.createObjectURL(imageBlob)

        setImgURL(url)


        const delResult = await fetch(`${base}delete/${file.name}`,{
            method: 'DELETE',
        }).then(r => r.json());
        console.log('results', delResult)

        setState("Submitted")
        setDisplayForm(false)
        setDisplayReturn(true)

        //navigate.push(`showImage?url=${url}`)


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

    async function testOnSubmit(e: React.SyntheticEvent){
        e.preventDefault()

        if (typeof file === 'undefined') return;

        console.log('file', file);
        console.log('label', label);

        const formData = new FormData();

        formData.append('file', file);
        formData.append('label', `${label}`)

        console.log(formData);

        const results = await fetch('http://localhost:8000/test',{
            method: 'POST',
            body: formData,
        }).then(r => r.json());
        console.log('results', results)

    }

    async function onReturn(e: React.SyntheticEvent){
        setDisplayReturn(false)
        setDisplayForm(true)
        setLabel(11)
        setPreview(null)
        setFile(undefined)
        setImgURL(undefined)
    }

    async function metrics(){
        setDisplayReturn(false)
        setDisplayForm(true)
        setLabel(11)
        setPreview(null)
        setFile(undefined)
        setImgURL(undefined)
        navigate.push(`/metrics`)

    }

    async function labelChange(e){
        
        console.log(e.target.value)

        setLabel(e.target.value)

    }

    // <form onSubmit={handleOnSubmit}>
    //             <input type="file" 
    //             name="image" 
    //             onChange={handleOnChange} 
    //             accept='image/jpeg, image/png'/>
    //             <img src={preview} />

    //             <button>Submit</button>
    //         </form>
    //         <img src={imgURL} />


    return(
        <div>
            
            {displayForm && (
                <>
                    <Card color="transparent" shadow={false}>
                        <Typography variant="h4" color="blue-gray">
                            MNIST number prediction
                        </Typography>
                        <Typography color="gray" className="mt-1 font-normal">
                            Upload a JPG or PNG image of a number to predict, labels provided will be stored for future training (optional).
                        </Typography>
                        <form className="mt-8 mb-2 w-80 max-w-screen-lg sm:w-96" onSubmit={handleOnSubmit}>

                            <div className="flex items-center justify-center w-full">
                                <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
                                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                        <svg className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" 
                                            strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                                        </svg>
                                        <p className="mb-2 text-sm text-gray-500 dark:text-gray-400"><span className="font-semibold">Click to upload</span></p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">PNG, JPG</p>
                                    </div>
                                    <input id="dropzone-file" type="file" className="hidden" name="image" 
                                    onChange={handleOnChange} 
                                    accept='image/jpeg, image/png'/>
                                </label>
                            </div> 

                            <div className='center'>
                                <img src={preview} className='center'/>
                            </div>

                                
                            
                            <label htmlFor="lbl" className="block mb-2 text-base font-medium text-white-900 dark:text-white">What number should it be?</label>
                            <select id="countries" className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" onChange={labelChange}>
                                <option defaultValue={11} value={11}>No Label</option>
                                <option value={0}>0</option>
                                <option value={1}>1</option>
                                <option value={2}>2</option>
                                <option value={3}>3</option>
                                <option value={4}>4</option>
                                <option value={5}>5</option>
                                <option value={6}>6</option>
                                <option value={7}>7</option>
                                <option value={8}>8</option>
                                <option value={9}>9</option>
                            </select>

                            <div>
                                <Button type='submit' className="mt-6 p-3" fullWidth >
                                Submit
                                </Button>
                            </div>
                    
                            
                            
                        </form>
                    </Card>
                    <Card>
                        <div>
                                <Button className="mt-6 p-3" fullWidth onClick={metrics}>
                                    Metrics
                                </Button>
                        </div>
                    </Card>
                </>
            )}

            {displayReturn && (
                <>
                    <Card color="transparent" shadow={false}>
                        <div className='center'>
                            <Typography variant="h4" color="blue-gray">
                                MNIST number prediction
                            </Typography>
                            <img src={imgURL} className='p-3 center'/>

                        </div>
                        <div>
                            <Button className="mt-6 p-3" fullWidth onClick={onReturn}>
                                Upload new image
                            </Button>
                        </div>
                        
                    </Card>

                    <Card>
                        <div>

                            <Button className="mt-6 p-3" fullWidth onClick={metrics}>
                                Metrics
                            </Button>

                        </div>
                    </Card>
                </>
            )}
        </div>
    )
}


export default upload;
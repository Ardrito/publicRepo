'use client'

import React, {useState} from 'react'
//import api from '../api'
import axios from 'axios';
import Home from './page';


export default function exp(){
    const [message, setMessage] = useState('');
    const [file, setFile] = useState<File | undefined>();


    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files){
            setFile(e.target.files[0])
        }  
    };

    const handleUpload = async () => {

    }


    return(
        <>
            <div className='input-group'>
                <input id='file' type='file' onChange={handleFileChange} />
            </div>
            {file && (
                <section>
                    File details:
                    <ul>
                        <li>Name: {file.name}</li>
                        <li>Type: {file.type}</li>
                        <li>Size: {file.size} bytes</li>
                    </ul>
                </section>
            )}

            {file && (
                <button
                onClick={handleUpload}
                className='submit'>
                    Upload a file
                </button>
            )}
        </>
    );
};
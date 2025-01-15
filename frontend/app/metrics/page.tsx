'use client'

import React, {useEffect, useState} from 'react';
import {
  Card,
  Button,
  Typography,
} from "@material-tailwind/react";
import {useParams, useRouter, useSearchParams} from 'next/navigation';

function displayMetrics(){
    const base = 'http://localhost:8001/metrics'
    const [metricsURL, setMetricsURL] = useState<string>();
    const [message, setMessage] = useState<string>("Message not received");
    let navigate = useRouter();

    async function getImage(){

        const fetchImage = await fetch(`${base}`,{
            method: 'GET',
        });
        const imageBlob = await fetchImage.blob();
        const url = URL.createObjectURL(imageBlob);

        setMetricsURL(url);

        const message = await fetch(`${base}/message`,{
            method: 'GET',
        }).then(r => r.json());
        setMessage(message);

    }

    function onReturn(){
        setMetricsURL(undefined)
        navigate.push(`/upload`)
    }

    useEffect(() => {
        getImage();
    },[]);


    return(
        <Card color="transparent" shadow={false}>
            <Typography variant="h4" color="blue-gray">
                Metrics
            </Typography>
            <img src={metricsURL} />

            <div className='p-5 textSmall'>
                <pre>
                    {message}
                </pre>

            </div>

            <Button className="mt-6" fullWidth onClick={onReturn}>
                Return to upload
            </Button>

        </Card>

    )
}

export default displayMetrics;
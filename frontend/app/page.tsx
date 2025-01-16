'use client'

import { useRouter } from "next/navigation";

import {
  Card,
  Button,
  Typography,
  CardBody,
  CardFooter,
} from "./exports";


export default function Home() {
  let navigate = useRouter();

  function visitApp(){
    navigate.push('/upload')

}

  return (
    <div className="text-center">
      <Card color='transparent'>
        <CardBody className="mt-6 w-150">
          <Typography variant="h4" color="blue-gray">
            Welcome to my home page, this is currently under maintenance but have a look at my most recent app deployment predicting hand drawn digits.
          </Typography>
        </CardBody>
        <CardFooter>
          <Button className='mt-6' onClick={visitApp}>
                Click here to visit my app
            </Button>
        </CardFooter>

      </Card>
    </div>
  );
}

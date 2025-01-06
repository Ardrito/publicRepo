import React, {useState, useEffect} from 'react'
//import api from '../api'
import axios from 'axios';
import Home from '.';

// export const main = async () =>{
//     async function main() {
//         try{
//             const response = await axios({
//                 method:'GET',
//                 url: 'http://localhost:8000/'
//             });
//             return response.data;
//         } catch(error) {
//             if (error.response) {
//                 console.log('error responded')
//             } else if (error.request) {
//                 console.log('no response')
//             }
//             console.log(error.config);
//             return (NaN)
//         }

//     }
//     return main()
// }


// const Home = () => {
//     const data = main()
//     return (
//         <div>
//             <h1>Data from API</h1>
//             <pre>{JSON.stringify(data, null, 2)}</pre>
//         </div>
//     );
// };

export default function exp(){
    const [message, setMessage] = useState('');
    useEffect(() => {
        const fetch = async () => {
            try{
                const response = await axios({
                    method:'GET',
                    url: 'http://localhost:8000/'
                });
                setMessage(response.data)
                
            } catch(error) {
                if (error.response) {
                    console.log('error responded')
                } else if (error.request) {
                    console.log('no response')
                }
                console.log(error.config);
                
            }

        }
        fetch();
    }, [])
    //const data = fetch()

    return(
        <h1> {message} </h1>
    )
}
FROM node:22-alpine

#copy source 


WORKDIR /app

COPY package*.json ./
#RUN sudo apt-get update

#RUN nvm install 22

# Install deps 
RUN npm install 

COPY . .

EXPOSE 3000


# Build 
RUN npm run build

ENTRYPOINT [ "npm", "start"]
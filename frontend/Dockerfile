FROM node:alpine

#copy source 
COPY . /app

WORKDIR /app

# Install deps 
RUN npm install 

# Build 
#RUN npm run build

ENTRYPOINT [ "npm", "run", "dev" ]
var express = require('express');
var router = express.Router();
const verifyToken = require('../verifyToken.js');
const jwt = require('jsonwebtoken');
const fs = require('fs');
const secretkey = require("../secretkey.js");

router.use(express.json())
router.use(express.urlencoded({ extended: false }))

function saveFiles(normal, abnormal){
    return new Promise((resolve, reject) => {
        for(let i=0; i < normal.length; i++){
            let file = normal[i];
            file = JSON.parse(file);
            let filename = file.name;
            let base64Data = file.thumbUrl.replace(/^data:image\/\w+;base64,/, "");
            let dataBuffer = new Buffer(base64Data, 'base64');
            let newname = `/home/lihui/medical-support/server/UserUpload/normal/${filename}`;
            
            fs.writeFile(newname, dataBuffer, err => {
                if(err){
                    console.log(err)
                    return reject(err)
                }
            })
        }

        for(let i=0; i < abnormal.length; i++){
            let file = abnormal[i];
            file = JSON.parse(file);
            let filename = file.name;
            let base64Data = file.thumbUrl.replace(/^data:image\/\w+;base64,/, "");
            let dataBuffer = new Buffer(base64Data, 'base64');
            let newname = `/home/lihui/medical-support/server/UserUpload/abnormal/${filename}`;
            
            fs.writeFile(newname, dataBuffer, err => {
                if(err){
                    console.log(err)
                    return reject(err)
                }
            })
        }

        return resolve();
    })
}

router.post("/", verifyToken, (req, res) => {
    jwt.verify(req.token, secretkey,async (err, authData) => {
        if(err)res.sendStatus(403)
        else{
            const {normalfiles, abnormalfiles} = req.body;
            await saveFiles(normalfiles, abnormalfiles).catch(err => res.sendStatus(500));
            res.sendStatus(200)
        }
    })
})

module.exports = router;
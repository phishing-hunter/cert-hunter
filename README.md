# Cert Hunter
This is the Docker image repository for validating [PHOps](https://github.com/phishing-hunter/PHOps).  
The algorithm of the engine that performs domain scoring running on [phishing-hunter](https://www.phishing-hunter.com) is available.  
If you need real-time notification of scoring results, please register an account [here](https://www.phishing-hunter.com/login).  

## Search History
* AWS S3
```bash
docker run --rm -it -v $PWD:/work -w /work \
    phishinghunter/cert-hunter:latest \
    bash -c 'cat /csv/target.csv|grep s3.amazonaws.com'
```

* AWS Cloudfront
```bash
docker run --rm -it -v $PWD:/work -w /work \
    phishinghunter/cert-hunter:latest \
    bash -c 'cat /csv/target.csv|grep cloudfront.net'
```

* GCP Cloud Run
```bash
docker run --rm -it -v $PWD:/work -w /work \
    phishinghunter/cert-hunter:latest \
    bash -c 'cat /csv/target.csv|grep run.app'
```

* Azure Web Apps
```bash
docker run --rm -it -v $PWD:/work -w /work \
    phishinghunter/cert-hunter:latest \
    bash -c 'cat /csv/target.csv|grep azurewebsites.net'
```

* Cloudflare
```bash
docker run --rm -it -v $PWD:/work -w /work \
    phishinghunter/cert-hunter:latest \
    bash -c 'cat /csv/target.csv|grep cloudflare.net'
```

## Reference
* [x0rz/phishing_catcher](https://github.com/x0rz/phishing_catcher)
* [stoerchl/yara_zip_module](https://github.com/stoerchl/yara_zip_module)
* [eth0izzle/bucket-stream](https://github.com/eth0izzle/bucket-stream)

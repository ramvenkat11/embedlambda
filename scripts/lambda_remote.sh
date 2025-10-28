#!/bin/bash

set -e


# Variables
LAYER_NAME="s2o-embed"
PYTHON_VERSION="python3.12"
OUTPUT_ZIP="package_embed.zip"
BASE_DIR=lambda
LAYER_DIR=$BASE_DIR/alayer
DIR=${LAYER_DIR}/python/lib/${PYTHON_VERSION}/site-packages
OUT_FILE=tmp.txt

ID_RSA="$HOME/aws_profile/id_rsa"
EC2_USER=ec2-user@18.211.164.21

copy_to() {
  echo "Copying $1 to /home/ec2-user/$2"
  scp -i $ID_RSA $1 $EC2_USER:/home/ec2-user/$2
}

copy_from() {
  echo "Copying from /home/ec2-user/$1 to $2"
  scp -i $ID_RSA $EC2_USER:/home/ec2-user/$1 $2
}

execr() {
  ssh -i $ID_RSA $EC2_USER $1
}

execr "rm -rf $BASE_DIR"
execr "mkdir -p $DIR"

echo "Gathering sources and packages used..."
copy_to "../*.py" $DIR/

TMP=tmp
mkdir $TMP
cp ../*.py $TMP/
pigar generate -f requirements.txt $TMP/
copy_to ./requirements.txt $BASE_DIR/
rm -rf $TMP

execr "pip install -r $BASE_DIR/requirements.txt --target=$DIR --python-version 3.12  --only-binary=:all: > $OUT_FILE"
echo "Downloaded packages"


execr "find $DIR -type d -name "__pycache__" -exec rm -rf {} +"
execr "find $DIR -type f -name "*.pyc" -delete"
execr "find $DIR -type f -name "*.pyo" -delete"
execr "find $DIR -type d -name "tests" -exec rm -rf {} +"
echo "Cleaned up"

execr "cd $LAYER_DIR && zip -r9 ../${OUTPUT_ZIP} ."
echo "Created zip"

copy_from $BASE_DIR/$OUTPUT_ZIP ./

RESPONSE=$(aws lambda publish-layer-version \
     --layer-name ${LAYER_NAME} \
     --description "search2o package" \
     --zip-file fileb://${OUTPUT_ZIP} \
     --compatible-runtimes ${PYTHON_VERSION})
LAYER_VERSION=$(echo "$RESPONSE" | jello -r "_.LayerVersionArn" | sed -e 's/\r$//')
echo "Published the new (layer) version $LAYER_VERSION"
rm -rf $OUTPUT_ZIP

for FUNCTION_NAME in getVectors; do
  FOO=$(aws lambda update-function-configuration \
      --function-name $FUNCTION_NAME \
      --layers "$LAYER_VERSION")
  echo "Attached "$LAYER_VERSION" to $FUNCTION_NAME"
done

execr "rm -rf $BASE_DIR"








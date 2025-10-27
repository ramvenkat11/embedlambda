#!/bin/bash

set -e

# Variables
LAYER_NAME="s2o-embed"
PYTHON_VERSION="python3.13"
OUTPUT_ZIP="package.zip"
FIRST_DIR=alayer
DIR=${FIRST_DIR}/python/lib/${PYTHON_VERSION}/site-packages
OUT_FILE=tmp.txt

rm -rf $FIRST_DIR
rm -f requirements.txt
rm -f ${OUTPUT_ZIP}
rm -f $OUT_FILE

mkdir -p $DIR

echo "Gathering sources and packages used..."
cp ../*.py $DIR/

pigar generate -f requirements.txt $DIR/
echo "Found following package dependencies:"
cat requirements.txt
echo

pip install -r requirements.txt --platform manylinux2014_aarch64 --target=$DIR --implementation cp \
    --python-version 3.13 --only-binary=:all:  > $OUT_FILE
echo "Downloaded packages"

(
  cd $FIRST_DIR || exit
  zip -r ../${OUTPUT_ZIP} -r .
)
echo "Created ${OUTPUT_ZIP}"


RESPONSE=$(aws lambda publish-layer-version \
     --layer-name ${LAYER_NAME} \
     --description "search2o embed package" \
     --zip-file fileb://${OUTPUT_ZIP} \
     --compatible-runtimes ${PYTHON_VERSION})
LAYER_VERSION=$(echo "$RESPONSE" | jello -r "_.LayerVersionArn" | sed -e 's/\r$//')
echo "Published the new (layer) version $LAYER_VERSION"

for FUNCTION_NAME in s2o s2osearch proxy; do
  FOO=$(aws lambda update-function-configuration \
      --function-name $FUNCTION_NAME \
      --layers "$LAYER_VERSION")
  echo "Attached "$LAYER_VERSION" to $FUNCTION_NAME"
done

rm -rf $FIRST_DIR
rm -f ${OUTPUT_ZIP}
rm -f $OUT_FILE
echo "Removed all generated files and directories"
#!/bin/bash
aws apprunner create-service \
  --service-name securiva-backend \
  --source-configuration file://apprunner-config.json \
  --instance-configuration '{"InstanceRoleArn":"arn:aws:iam::281505305629:role/securiva-apprunner-instance-role"}' \
  --health-check-configuration '{"Protocol":"TCP","Interval":10,"Timeout":5,"HealthyThreshold":1,"UnhealthyThreshold":5}' \
  --region us-east-2

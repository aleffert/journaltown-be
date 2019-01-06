# Journal town backend

## Setup
```make docker-init```

## Running
```make docker-start```

Or for interactive running
```make docker-ssh```

## Testing
```make docker-test```

# Changing Secrets

```
gcloud kms encrypt \
  --plaintext-file=infrastructure/terraform/secrets-<environment>.tfvars \
  --ciphertext-file=infrastructure/terraform/secrets-<environment>.tfvars.enc \
  --location=global \
  --keyring=journaltown \
  --key=journaltown
```

For example, for the `staging` environment:

```
gcloud kms encrypt \
  --plaintext-file=infrastructure/terraform/secrets-staging.tfvars \
  --ciphertext-file=infrastructure/secrets-staging.tfvars.enc \
  --location=global \
  --keyring=journaltown \
  --key=journaltown
```
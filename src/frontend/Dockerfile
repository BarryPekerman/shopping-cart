# Stage 0: render nginx.conf
FROM nginx:alpine AS renderer

RUN apk add --no-cache gettext

# Build-time variables—defaults can be overridden via `--build-arg`
ARG BACKEND_HOST=localhost
ARG BACKEND_PORT=5000

WORKDIR /tmp

COPY nginx.conf.template .

# Render the template now
RUN envsubst '\$BACKEND_HOST \$BACKEND_PORT' \
      < nginx.conf.template \
      > nginx.conf

# Stage 1: final image
FROM nginx:alpine

WORKDIR /usr/share/nginx/html
# Copy static assets
COPY ./*.html ./
COPY ./*.css  ./
COPY ./*.js   ./

# Copy the pre-rendered nginx.conf
COPY --from=renderer /tmp/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


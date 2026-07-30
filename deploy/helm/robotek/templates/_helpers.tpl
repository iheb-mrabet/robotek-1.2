{{/*
Return the chart name.
*/}}
{{- define "robotek.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Return the fully qualified application name.
*/}}
{{- define "robotek.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Return the chart name and chart version.
*/}}
{{- define "robotek.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common Kubernetes labels.
*/}}
{{- define "robotek.labels" -}}
helm.sh/chart: {{ include "robotek.chart" . }}
{{ include "robotek.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
{{- end }}

{{/*
Stable labels used by the Deployment selector.
*/}}
{{- define "robotek.selectorLabels" -}}
app.kubernetes.io/name: {{ include "robotek.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Return the ServiceAccount name.
*/}}
{{- define "robotek.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "robotek.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Return an immutable digest reference when a digest is supplied.
Otherwise, use the configured image tag.
*/}}
{{- define "robotek.image" -}}
{{- if .Values.image.digest }}
{{- printf "%s@%s" .Values.image.repository .Values.image.digest }}
{{- else }}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- end }}
{{- end }}
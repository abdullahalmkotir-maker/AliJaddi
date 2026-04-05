function isImageUrl(path: string) {
  return /\.(jpe?g|png|gif|webp)$/i.test(path);
}

function isPdfUrl(path: string) {
  return /\.pdf$/i.test(path);
}

export function XrayPreviewContent({ url, label }: { url: string | null; label: string }) {
  if (url && isImageUrl(url)) {
    return (
      <img
        src={url}
        alt={label}
        style={{
          marginTop: "1rem",
          maxWidth: "100%",
          borderRadius: 3,
          border: "1px solid var(--border)",
        }}
      />
    );
  }
  if (url && isPdfUrl(url)) {
    return (
      <div style={{ marginTop: "1rem" }}>
        <a className="btn btn-primary" href={url} target="_blank" rel="noreferrer">
          فتح ملف PDF في نافذة جديدة
        </a>
      </div>
    );
  }
  return (
    <div
      style={{
        marginTop: "1rem",
        minHeight: 160,
        background: "var(--surface-2)",
        borderRadius: 3,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        border: "1px dashed var(--border)",
        color: "var(--muted)",
        padding: "1rem",
        textAlign: "center",
      }}
    >
      {url
        ? "تعذر عرض هذا النوع من الملفات هنا."
        : "لا يوجد ملف مرفوع لهذه الجلسة — يظهر الوصف فقط."}
    </div>
  );
}

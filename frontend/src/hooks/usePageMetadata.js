import { useEffect } from 'react'

function usePageMetadata(title, description) {
  useEffect(() => {
    document.title = title

    const metaDescription =
      description.length > 160
        ? `${description.slice(0, 157).trimEnd()}...`
        : description
    let descriptionMeta = document.querySelector('meta[name="description"]')
    if (!descriptionMeta) {
      descriptionMeta = document.createElement('meta')
      descriptionMeta.name = 'description'
      document.head.append(descriptionMeta)
    }

    descriptionMeta.content = metaDescription
  }, [description, title])
}

export default usePageMetadata

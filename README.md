# Eventide RAG

This is a chat server that uses the http://docs.eventide-project.org/ docsite to provide help for people building Eventide projects.

## Index Docs

It was a bit of a challenge to get something to crawl the docsite well and download them, but since it's an open-source repo, I was able to just clone the docsite, then parse all of the markdown files into the index.

There were some oddities/surprises about how the Markdown parser works in combination with the DirectoryLoader, but it got into a structured data object.

        Document(
            page_content="Every event stream records the lifecycle events of a single [entity](./services/entities.md).  \nEach activity of an entity's life is recorded as an event, and written to the entity's stream.  \n![Publish and Subscribe](../images/event-stream.png)",
            metadata={
                'Header 1': 'Event Sourcing',
                'Header 2': 'Event Streams and Entities',
                'source': 'docs/core-concepts/event-sourcing.md'
            }
        )

Then the embedding used the OpenAI's "text-embedding-3-large".

I used FAISS for the vectorstore and have the whole vector database in this repo (it's like 10 megs, sorry github).



from app.model.response import CompareResponse, ComparisonResult
from fastapi import APIRouter
from app.model.request import CompareRequest

router = APIRouter(prefix="/symmetry/v1", tags=["comparison"])

@router.post("/articles/compare", response_model=CompareResponse)
def compare_articles(payload: CompareRequest):
    """
    This endpoint requests a comparison of two blobs of text.
    The request includes the articles, the languages of the articles, the comparison threshold, and model name.

    The response is an array of comparison results, allowing support for a future state where
    output may be requested from multiple ML models in a single request.
    """

    left_article_array = [
        "Barack Hussein Obama II is an American politician who served as the 44th president of the United States from 2009 to 2017.",
        "Obama previously served as a U.S. senator representing Illinois from 2005 to 2008 and as an Illinois state senator from 1997 to 2004.",
        "Obama was born in Honolulu, Hawaii.",
        "He graduated from Columbia University in 1983 with a Bachelor of Arts degree in political science and later worked as a community organizer in Chicago.",
        "In 1988, Obama enrolled in Harvard Law School, where he was the first black president of the Harvard Law Review.",
        "In the 2008 presidential election, after a close primary campaign against Hillary Clinton, he was nominated by the Democratic Party for president.",
        "Obama selected Joe Biden as his running mate and defeated Republican nominee John McCain and his running mate Sarah Palin."
    ]

    right_article_array = [
        "Barack Hussein Obama II is an American politician who served as the 44th president of the United States from 2009 to 2017.",
        "A member of the Democratic Party, he was the first African-American president in American history.",
        "He graduated from Columbia University in 1983 with a Bachelor of Arts degree in political science and later worked as a community organizer in Chicago.",
        "In 1988, Obama enrolled in Harvard Law School, where he was the first black president of the Harvard Law Review.",
        "He became a civil rights attorney and an academic, teaching constitutional law at the University of Chicago Law School from 1992 to 2004.",
        "In 1996, Obama was elected to represent the 13th district in the Illinois Senate, a position he held until 2004, when he successfully ran for the U.S. Senate.",
        "In the 2008 presidential election, after a close primary campaign against Hillary Clinton, he was nominated by the Democratic Party for president."
    ]

    comparison = ComparisonResult(
        left_article_array=left_article_array,
        right_article_array=right_article_array,
        left_article_missing_info_index=[1, 2, 6],  # Dummy indices
        right_article_extra_info_index=[1, 4, 5]    # Dummy indices
    )

    return CompareResponse(comparisons=[comparison])

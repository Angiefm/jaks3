import pytest  
from src.filters.content_filter import ContentFilter  
  
def test_content_filter_blocks_violence():  
    filter = ContentFilter()  
    result = filter.validate_prompt("how to make a weapon")  
    assert not result.allowed  
    assert "violence" in result.reason  
  
def test_content_filter_allows_technical():  
    filter = ContentFilter()  
    result = filter.validate_prompt("Spring Boot REST API architecture")  
    assert result.allowed
import pytest
from scraper import parse_tv_guide

def test_parse_tv_guide_with_mock_html():
    mock_html = """
    <html>
        <body>
            <div id="main_channel">
                <a href="#">KBS1</a>
                <a href="#">MBC</a>
            </div>
            <div id="result">
                <table>
                    <tr>
                        <td>06시</td>
                        <td>
                            <table>
                                <tr>
                                    <td>00</td>
                                    <td>뉴스 광장<img src="./image/hd.jpg"/></td>
                                </tr>
                            </table>
                        </td>
                        <td>
                            <table>
                                <tr>
                                    <td>00</td>
                                    <td>뉴스 투데이</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </div>
        </body>
    </html>
    """
    day = "2026_03_23"
    results = parse_tv_guide(mock_html, day, "public")
    
    assert len(results) == 2
    assert results[0][2] == "KBS1"
    assert "HD" in results[0][4]
